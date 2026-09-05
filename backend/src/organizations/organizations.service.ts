import {
  ConflictException,
  Injectable,
  NotFoundException,
} from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service.js';
import { MembershipRole } from '../generated/prisma/enums.js';
import type { CreateOrganizationDto } from './dto/create-organization.dto.js';
import type { InviteMemberDto } from './dto/invite-member.dto.js';

// Rango Unicode de marcas diacríticas combinantes (U+0300 a U+036F), producidas
// por normalize('NFD') al separar una letra acentuada de su acento.
const COMBINING_DIACRITICS = new RegExp('[̀-ͯ]', 'g');

function slugify(name: string): string {
  return name
    .toLowerCase()
    .normalize('NFD')
    .replace(COMBINING_DIACRITICS, '') // quita acentos
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

@Injectable()
export class OrganizationsService {
  constructor(private readonly prisma: PrismaService) {}

  /** Crea la organización y a su creador como OWNER, en una sola transacción. */
  async create(ownerId: string, dto: CreateOrganizationDto) {
    const baseSlug = dto.slug ?? slugify(dto.name);
    const slug = await this.resolveAvailableSlug(baseSlug);

    return this.prisma.$transaction(async (tx) => {
      const organization = await tx.organization.create({
        data: { name: dto.name, slug },
      });

      await tx.membership.create({
        data: {
          organizationId: organization.id,
          userId: ownerId,
          role: MembershipRole.OWNER,
        },
      });

      await tx.auditLog.create({
        data: {
          action: 'organization.created',
          targetType: 'Organization',
          targetId: organization.id,
          actorUserId: ownerId,
          organizationId: organization.id,
        },
      });

      return organization;
    });
  }

  /** Organizaciones a las que pertenece el usuario, con su rol en cada una. */
  async findMine(userId: string) {
    const memberships = await this.prisma.membership.findMany({
      where: { userId },
      include: { organization: true },
      orderBy: { createdAt: 'asc' },
    });

    return memberships.map((m) => ({ ...m.organization, role: m.role }));
  }

  async findOne(organizationId: string) {
    const organization = await this.prisma.organization.findUnique({
      where: { id: organizationId },
    });
    if (!organization) {
      throw new NotFoundException('Organización no encontrada.');
    }
    return organization;
  }

  async listMembers(organizationId: string) {
    return this.prisma.membership.findMany({
      where: { organizationId },
      include: { user: { select: { id: true, email: true, name: true } } },
      orderBy: { createdAt: 'asc' },
    });
  }

  /** Agrega como miembro a un usuario ya existente. No crea cuentas nuevas. */
  async inviteMember(organizationId: string, dto: InviteMemberDto) {
    const user = await this.prisma.user.findUnique({
      where: { email: dto.email },
    });
    if (!user) {
      throw new NotFoundException(
        'No existe un usuario registrado con ese correo.',
      );
    }

    const existingMembership = await this.prisma.membership.findUnique({
      where: { userId_organizationId: { userId: user.id, organizationId } },
    });
    if (existingMembership) {
      throw new ConflictException(
        'El usuario ya pertenece a esta organización.',
      );
    }

    return this.prisma.membership.create({
      data: {
        organizationId,
        userId: user.id,
        role: dto.role ?? MembershipRole.MEMBER,
      },
    });
  }

  private async resolveAvailableSlug(base: string): Promise<string> {
    let candidate = base;
    let attempt = 0;

    while (
      await this.prisma.organization.findUnique({ where: { slug: candidate } })
    ) {
      attempt += 1;
      candidate = `${base}-${attempt}`;
    }

    return candidate;
  }
}
