import { IsEmail, IsEnum, IsOptional } from 'class-validator';
import { MembershipRole } from '../../generated/prisma/enums.js';

export class InviteMemberDto {
  @IsEmail()
  email!: string;

  @IsOptional()
  @IsEnum(MembershipRole)
  role?: MembershipRole;
}
